import React from 'react';
import { connect } from 'react-redux';

import { selectCollection } from 'src/selectors';
import CollectionContextLoader from 'src/components/Collection/CollectionContextLoader';
import CollectionToolbar from 'src/components/Collection/CollectionToolbar';
import CollectionInfoMode from 'src/components/Collection/CollectionInfoMode';
import CollectionXrefIndexMode from 'src/components/Collection/CollectionXrefIndexMode';
import CollectionDocumentsMode from 'src/components/Collection/CollectionDocumentsMode';
import { DualPane, SectionLoading, ErrorSection } from 'src/components/common';
import Preview from 'src/components/Preview/Preview';
import CollectionViewsMenu from "../ViewsMenu/CollectionViewsMenu";


class PreviewCollection extends React.Component {
  render() {
    const { previewId } = this.props;
    return (
      <CollectionContextLoader collectionId={previewId}>
        {this.renderContext()}
      </CollectionContextLoader>
    );
  }

  renderContext() {
    const { collection, previewMode = 'info' } = this.props;
    let mode = null, maximised = true;
    if (collection.isError) {
      mode = <ErrorSection error={collection.error} />
    } else if (collection.id === undefined) {
      mode = <SectionLoading/>;
    } else if (previewMode === 'xref') {
      mode = <CollectionXrefIndexMode collection={collection} />;
      maximised = true;
    } else if (previewMode === 'documents') {
      mode = <CollectionDocumentsMode collection={collection} />;
      maximised = true;
    } else {
      mode = <CollectionInfoMode collection={collection} />;
    }
    return (
      <Preview maximised={maximised}>
        {/*<CollectionViewsMenu collection={collection}
                            activeMode={previewMode}
                            isPreview={true} />*/}
        <DualPane.InfoPane className="with-heading">
          <CollectionToolbar collection={collection}
                            isPreview={true} />
          <CollectionInfoMode collection={collection}/>
          <CollectionViewsMenu collection={collection}
                               activeMode={previewMode}
                               isPreview={true} />
        </DualPane.InfoPane>
      </Preview>
    );
  }
}


const mapStateToProps = (state, ownProps) => {
  return {
    collection: selectCollection(state, ownProps.previewId)
  };
};

PreviewCollection = connect(mapStateToProps, {})(PreviewCollection);
export default PreviewCollection;